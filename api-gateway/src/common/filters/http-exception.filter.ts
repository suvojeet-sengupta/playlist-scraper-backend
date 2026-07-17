import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  Logger,
} from '@nestjs/common';
import { Response } from 'express';
import { ApiResponseDto } from '../dto/api-response.dto';

@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: HttpException, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const status = exception.getStatus();
    const exceptionResponse = exception.getResponse();

    let message: string;
    let details: unknown;

    if (typeof exceptionResponse === 'string') {
      message = exceptionResponse;
    } else if (typeof exceptionResponse === 'object') {
      const resp = exceptionResponse as Record<string, unknown>;
      message =
        (resp['message'] as string) ??
        (resp['error'] as string) ??
        exception.message;
      details = resp['details'] ?? resp['message'];
    } else {
      message = exception.message;
    }

    this.logger.error(`HTTP ${status} – ${message}`);

    const body = ApiResponseDto.error(
      `HTTP_${status}`,
      Array.isArray(message) ? message.join('; ') : message,
      details,
    );

    response.status(status).json(body);
  }
}
