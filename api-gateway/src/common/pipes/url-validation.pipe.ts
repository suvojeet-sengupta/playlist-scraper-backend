import {
  PipeTransform,
  Injectable,
  BadRequestException,
} from '@nestjs/common';

/** URL patterns for supported music platforms. */
const SUPPORTED_PATTERNS = [
  { platform: 'Spotify', regex: /open\.spotify\.com\/playlist\// },
  { platform: 'Apple Music', regex: /music\.apple\.com\/.+\/playlist\// },
  { platform: 'YouTube Music', regex: /music\.youtube\.com\/playlist/ },
];

@Injectable()
export class UrlValidationPipe implements PipeTransform<string, string> {
  transform(value: string): string {
    if (!value) {
      throw new BadRequestException('A playlist URL is required.');
    }

    const isSupported = SUPPORTED_PATTERNS.some((p) => p.regex.test(value));
    if (!isSupported) {
      const supported = SUPPORTED_PATTERNS.map((p) => p.platform).join(', ');
      throw new BadRequestException(
        `Unsupported playlist URL. Currently supported platforms: ${supported}.`,
      );
    }

    return value;
  }
}
