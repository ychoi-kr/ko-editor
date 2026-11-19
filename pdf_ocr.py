import argparse
import os
import shutil
import sys
import tempfile

from natsort import natsorted


def _find_korean_font():
    """플랫폼별 한글 폰트 경로를 반환한다."""
    candidates = []
    if sys.platform == "win32":
        candidates = [
            "C:/Windows/Fonts/malgun.ttf",
            "C:/Windows/Fonts/gulim.ttc",
            "C:/Windows/Fonts/batang.ttc",
        ]
    elif sys.platform == "darwin":
        candidates = [
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/Library/Fonts/AppleGothic.ttf",
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"한글 폰트를 찾을 수 없습니다. 검색 경로: {candidates}")


def _ocr_easyocr(img_bytes):
    """EasyOCR로 이미지에서 텍스트와 위치를 추출한다. [(bbox, text), ...]"""
    import warnings
    import easyocr
    import torch
    if not hasattr(_ocr_easyocr, "_reader"):
        use_gpu = torch.cuda.is_available()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            _ocr_easyocr._reader = easyocr.Reader(["ko", "en"], gpu=use_gpu, verbose=False)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        results = _ocr_easyocr._reader.readtext(img_bytes)
    return [(bbox, text) for bbox, text, conf in results if conf >= 0.3]


def _ocr_ollocr(img_bytes):
    """ollocr로 이미지에서 텍스트와 위치를 추출한다. [(bbox, text), ...]"""
    import io
    import json
    import re
    import ollocr
    from PIL import Image

    img = Image.open(io.BytesIO(img_bytes))
    w, h = img.size

    raw = ollocr.ask(img_bytes,
        f"이 이미지는 {w}x{h} 픽셀이다. "
        "모든 텍스트 영역을 추출하라. 수식은 LaTeX 표기로 변환하라. "
        "JSON 배열로 반환하되, 각 요소는 "
        '"bbox" (이미지 픽셀 좌표 기준 [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]), '
        '"text" (인식된 텍스트)를 포함하라. '
        f"bbox 좌표는 반드시 0~{w}(x), 0~{h}(y) 범위 내여야 한다. "
        "JSON만 반환하고 설명은 하지 마라."
    )

    # JSON 파싱
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```\w*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw).strip()
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            try:
                items = json.loads(match.group())
            except json.JSONDecodeError:
                print(f"    bbox 추출 실패, 텍스트만 추출 시도...", flush=True)
                items = []
        else:
            print(f"    bbox 추출 실패, 텍스트만 추출 시도...", flush=True)
            items = []

    results = []
    for item in items:
        text = item.get("text", "").strip().strip('"\'\u201c\u201d\u2018\u2019\u200b \t')
        bbox = item.get("bbox")
        if text:
            results.append((bbox, text))

    # bbox 응답 실패 시 텍스트만이라도 추출
    if not results:
        text = ollocr.image_to_latex(img_bytes)
        text = text.strip().strip('"\'\u201c\u201d\u2018\u2019\u200b \t')
        if text:
            results.append((None, text))

    return results


def _insert_text(page, img_rect, img_w, img_h, ocr_results, ko_font):
    """OCR 결과를 페이지에 투명 텍스트로 삽입한다."""
    import fitz
    added = 0

    scale_x = img_rect.width / img_w
    scale_y = img_rect.height / img_h

    for bbox, text in ocr_results:
        if bbox is not None:
            x0 = img_rect.x0 + min(p[0] for p in bbox) * scale_x
            y0 = img_rect.y0 + min(p[1] for p in bbox) * scale_y
            x1 = img_rect.x0 + max(p[0] for p in bbox) * scale_x
            y1 = img_rect.y0 + max(p[1] for p in bbox) * scale_y
            rect = fitz.Rect(x0, y0, x1, y1)
            fontsize = (y1 - y0) * 0.8
        else:
            rect = img_rect
            fontsize = 10

        if rect.is_empty or rect.is_infinite or fontsize < 1:
            continue
        # fontsize를 줄여가며 rect에 맞춤
        for attempt_size in [fontsize, fontsize * 0.5, fontsize * 0.25]:
            if attempt_size < 1:
                attempt_size = 1
            rc = page.insert_textbox(
                rect, text,
                fontname="ko",
                fontfile=ko_font,
                fontsize=attempt_size,
                color=(0, 0, 0),
                render_mode=3,
            )
            if rc >= 0:
                break
        added += len(text)
    return added


def make_searchable(input_pdf, output_pdf, ocr_engine="easyocr"):
    """OCR images in each page and add invisible text layer."""
    import fitz

    ocr_fn = _ocr_easyocr if ocr_engine == "easyocr" else _ocr_ollocr
    ko_font = _find_korean_font()
    doc = fitz.open(input_pdf)
    try:
        for i, page in enumerate(doc):
            images = page.get_images()
            if not images:
                print(f"  {i + 1}/{len(doc)} 페이지 → 0개 이미지", flush=True)
                continue

            added = 0
            for img in images:
                xref = img[0]
                rects = page.get_image_rects(xref)
                if not rects:
                    continue
                img_rect = rects[0]

                img_data = doc.extract_image(xref)
                img_bytes = img_data["image"]
                results = ocr_fn(img_bytes)
                if not results:
                    continue

                added += _insert_text(
                    page, img_rect,
                    img_data["width"], img_data["height"],
                    results, ko_font,
                )

            print(f"  {i + 1}/{len(doc)} 페이지 → {len(images)}개 이미지, +{added}자", flush=True)
        doc.subset_fonts()
        doc.ez_save(output_pdf)
    finally:
        doc.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="PDF 이미지에서 텍스트를 추출하여 검색 가능한 PDF를 생성한다.",
        epilog="""사용 예:
  pdf_ocr "[교안]소방유체역학-03.pdf" --engine ollocr
  bash:  for f in [교안]소방유체역학-*.pdf; do pdf_ocr "$f" --engine ollocr; done
  cmd:   for %%f in ([교안]소방유체역학-*.pdf) do pdf_ocr "%%f" --engine ollocr""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", help="처리할 PDF 파일")
    parser.add_argument("--engine", choices=["easyocr", "ollocr"], default="easyocr",
                        help="OCR 엔진 (기본: easyocr)")
    args = parser.parse_args()

    filepath = args.file
    if not os.path.exists(filepath):
        print(f"파일 없음: {filepath}")
        sys.exit(1)

    directory = os.path.dirname(filepath) or "."
    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)

    if name.startswith("searchable_"):
        print(f"건너뜀 (이미 searchable): {basename}")
        sys.exit(0)

    dest = os.path.join(directory, f"searchable_{name}{ext}")
    if os.path.exists(dest):
        print(f"건너뜀 (이미 존재): searchable_{name}{ext}")
        sys.exit(0)

    print(f"처리 중: {basename}")
    with tempfile.TemporaryDirectory() as tmp_dir:
        local_f = os.path.join(tmp_dir, basename)
        shutil.copy2(filepath, local_f)
        tmp_out = os.path.join(tmp_dir, f"searchable_{name}{ext}")
        make_searchable(local_f, tmp_out, ocr_engine=args.engine)
        shutil.copy2(tmp_out, dest)
    print(f"완료: searchable_{name}{ext}")
