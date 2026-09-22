/** The few ways a number is written on more than one screen. */

export const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

/** A task's number as the catalogue prints it: `007`. */
export const topicNo = (topic: number) => String(topic).padStart(3, "0");

/** A stretch of active time: `45s`, `3m07s`. */
export const secs = (n: number) => n >= 60 ? `${Math.floor(n / 60)}m${String(n % 60).padStart(2, "0")}s` : `${n}s`;
