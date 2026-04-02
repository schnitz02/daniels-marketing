/**
 * Date/time formatting utilities — all output in Melbourne time (Australia/Melbourne).
 */

const TZ = "Australia/Melbourne"
const LOCALE = "en-AU"

/** "1 Jan 2026" */
export function formatDate(value) {
  if (!value) return ""
  return new Date(value).toLocaleDateString(LOCALE, {
    day: "numeric", month: "short", year: "numeric",
    timeZone: TZ,
  })
}

/** "1 Jan 2026, 3:45 pm" */
export function formatDateTime(value) {
  if (!value) return ""
  return new Date(value).toLocaleString(LOCALE, {
    day: "numeric", month: "short", year: "numeric",
    hour: "numeric", minute: "2-digit", hour12: true,
    timeZone: TZ,
  })
}

/** "3:45 pm" */
export function formatTime(value) {
  if (!value) return ""
  return new Date(value).toLocaleTimeString(LOCALE, {
    hour: "numeric", minute: "2-digit", hour12: true,
    timeZone: TZ,
  })
}

/** "1 Jan" (for chart tick labels) */
export function formatDateShort(value) {
  if (!value) return ""
  return new Date(value).toLocaleDateString(LOCALE, {
    day: "numeric", month: "short",
    timeZone: TZ,
  })
}

/** "Jan '26" (for monthly chart ticks) */
export function formatMonthYear(value) {
  if (!value) return ""
  return new Date(value).toLocaleDateString(LOCALE, {
    month: "short", year: "2-digit",
    timeZone: TZ,
  })
}
