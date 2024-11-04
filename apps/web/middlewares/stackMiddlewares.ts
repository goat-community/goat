import type { NextMiddleware } from "next/server";
import { NextResponse } from "next/server";

import type { MiddlewareFactory } from "./types";

export function stackMiddlewares(functions: MiddlewareFactory[] = [], index = 0): NextMiddleware {
  const current = functions[index];
  if (current) {
    const next = stackMiddlewares(functions, index + 1);
    return current(next);
  }
  return () => NextResponse.next();
}
