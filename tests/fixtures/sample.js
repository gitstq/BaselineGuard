// const legacy = document.write("inside a whole-line comment");
const url = "https://example.com/api";

async function load() {
  const res = await fetch(url);
  const data = await res.json();
  return structuredClone(data);
}

class FancyCard extends HTMLElement {}

const last = [1, 2, 3].at(-1);
const maybe = data?.items?.[0] ?? [];
