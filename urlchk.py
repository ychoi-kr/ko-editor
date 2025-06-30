#!/usr/bin/python3

import sys
import re
import urllib.request
import urllib.error
from urllib.parse import urlparse
import argparse
from pathlib import Path

# 기존 코드에서 가져온 모듈들
from common_io import read_input, write_output, read_file, write_file, get_file_paths_from_args
import docx2txt


def extract_urls(text):
    """텍스트에서 URL을 추출합니다."""
    # URL 정규식 패턴 (http, https, ftp 등을 포함)
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    raw_urls = re.findall(url_pattern, text)
    
    # 한국어 조사 제거
    korean_particles = [
        '은', '는', '이', '가', '을', '를', '에', '에서', '로', '으로',
        '와', '과', '의', '도', '만', '까지', '부터', '보다', '처럼',
        '마다', '조차', '라도', '라든지', '든지', '라면', '면서'
    ]
    
    cleaned_urls = []
    for url in raw_urls:
        cleaned_url = url
        
        # 영문 문장 끝 구두점 제거 (마침표, 쉼표, 세미콜론, 콜론, 느낌표, 물음표)
        while cleaned_url and cleaned_url[-1] in '.,;:!?':
            cleaned_url = cleaned_url[:-1]
        
        # URL 끝에 한국어 조사가 붙어있는지 확인하고 제거
        for particle in korean_particles:
            if cleaned_url.endswith(particle):
                cleaned_url = cleaned_url[:-len(particle)]
                break
        
        # 다시 한번 구두점 제거 (조사 제거 후에도 구두점이 남을 수 있음)
        while cleaned_url and cleaned_url[-1] in '.,;:!?':
            cleaned_url = cleaned_url[:-1]
            
        if cleaned_url:  # 빈 문자열이 아닌 경우만 추가
            cleaned_urls.append(cleaned_url)
    
    # 중복 제거하면서 순서 유지
    seen = set()
    unique_urls = []
    for url in cleaned_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls


def check_url(url, timeout=10):
    """URL에 접근을 시도하고 결과를 반환합니다."""
    try:
        # User-Agent 헤더 추가 (일부 사이트에서 봇 차단 방지)
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            content_type = response.headers.get('Content-Type', 'Unknown')
            return {
                'status': 'SUCCESS',
                'code': status_code,
                'content_type': content_type,
                'error': None
            }
    
    except urllib.error.HTTPError as e:
        return {
            'status': 'HTTP_ERROR',
            'code': e.code,
            'content_type': None,
            'error': str(e)
        }
    
    except urllib.error.URLError as e:
        return {
            'status': 'URL_ERROR',
            'code': None,
            'content_type': None,
            'error': str(e)
        }
    
    except Exception as e:
        return {
            'status': 'ERROR',
            'code': None,
            'content_type': None,
            'error': str(e)
        }


def read_text_content(input_file):
    """파일에서 텍스트 내용을 읽습니다."""
    if input_file.endswith('.docx'):
        try:
            return docx2txt.process(input_file)
        except Exception as e:
            print(f"Error reading docx file: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif input_file.endswith('.txt'):
        try:
            content = read_file(input_file)
            return ''.join(content)
        except Exception as e:
            print(f"Error reading txt file: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        print(f"Unsupported file type: {input_file}", file=sys.stderr)
        print("Supported formats: .txt, .docx", file=sys.stderr)
        sys.exit(1)


def format_result(url, result):
    """결과를 포맷팅합니다."""
    status_symbols = {
        'SUCCESS': '✓',
        'HTTP_ERROR': '✗',
        'URL_ERROR': '✗',
        'ERROR': '✗'
    }
    
    symbol = status_symbols.get(result['status'], '?')
    
    if result['status'] == 'SUCCESS':
        return f"{symbol} {url} (HTTP {result['code']}, {result['content_type']})"
    else:
        error_info = f"HTTP {result['code']}" if result['code'] else result['error']
        return f"{symbol} {url} ({error_info})"


def main():
    parser = argparse.ArgumentParser(
        description='텍스트에서 URL을 추출하고 접근 가능성을 테스트합니다.',
        epilog='입력: 표준입력, .txt 파일, 또는 .docx 파일'
    )
    parser.add_argument('input_file', nargs='?', help='입력 파일 (.txt 또는 .docx)')
    parser.add_argument('-o', '--output', help='결과를 저장할 파일')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='타임아웃 (초, 기본값: 10)')
    parser.add_argument('--urls-only', action='store_true', help='URL만 출력 (테스트하지 않음)')
    
    args = parser.parse_args()
    
    # 입력 읽기
    if args.input_file:
        if not Path(args.input_file).exists():
            print(f"File not found: {args.input_file}", file=sys.stderr)
            sys.exit(1)
        text = read_text_content(args.input_file)
    else:
        text = read_input()
    
    # URL 추출
    urls = extract_urls(text)
    
    if not urls:
        print("No URLs found in the input.")
        return
    
    print(f"Found {len(urls)} unique URL(s):")
    print()
    
    results = []
    
    for i, url in enumerate(urls, 1):
        if args.urls_only:
            result_line = f"{i:2d}. {url}"
            print(result_line)
            results.append(result_line)
        else:
            print(f"{i:2d}. Testing {url}...", end=" ", flush=True)
            result = check_url(url, timeout=args.timeout)
            result_line = format_result(url, result)
            print(result_line)
            results.append(result_line)
    
    # 결과 저장
    if args.output:
        try:
            write_file(args.output, [line + '\n' for line in results])
            print(f"\nResults saved to: {args.output}")
        except Exception as e:
            print(f"Error saving results: {e}", file=sys.stderr)
    
    # 요약 출력 (테스트 모드일 때만)
    if not args.urls_only and len(urls) > 1:
        print()
        print("Summary:")
        success_count = sum(1 for line in results if line.startswith('✓'))
        error_count = len(urls) - success_count
        print(f"  Successful: {success_count}")
        print(f"  Failed: {error_count}")


if __name__ == "__main__":
    main()
