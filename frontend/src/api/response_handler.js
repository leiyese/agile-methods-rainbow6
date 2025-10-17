export const parseAnswer = (data = {}) => {
  const answer = data.answer ?? "";
  const rawSources = Array.isArray(data.sources) ? data.sources : [];

  const seen = new Set();
  const sources = [];

  for (const src of rawSources) {
    const rawExcerpt = src.excerpt ?? src.content ?? "";
    const excerptText = String(rawExcerpt || "").trim();

    const rubrikMatch = excerptText.match(/Rubrik:\s*(.+?)(?:\r?\n|$)/i);
    const section_title = rubrikMatch
      ? rubrikMatch[1].trim()
      : (excerptText.split(/\r?\n/).find((l) => l.trim()) || "").trim() || null;

    const document = (src.document ?? src.filename ?? "").toString().trim();
    const key = `${document.toLowerCase()}|${(section_title || "")
      .toString()
      .toLowerCase()}`;

    if (seen.has(key)) continue;
    seen.add(key);

    sources.push({
      document: document || null,
      section_title,
    });
  }

  return {
    answer,
    sources,
    raw: data,
  };
};
