import { test } from "node:test";
import assert from "node:assert/strict";
import { countries, bySlug, byCca3, neighbours, regions } from "./countries.ts";

test("slugs are unique, lowercase and derived from the name", () => {
  const seen = new Set<string>();
  for (const c of countries) {
    assert.equal(c.slug, c.slug.toLowerCase(), `${c.slug} is not lowercase`);
    assert.equal(
      c.slug,
      c.name.toLowerCase().replace(/[^a-z]+/g, "-"),
      `${c.name} does not match its slug`,
    );
    assert.ok(!seen.has(c.slug), `duplicate slug ${c.slug}`);
    seen.add(c.slug);
    assert.ok(bySlug(c.slug), `bySlug misses ${c.slug}`);
    assert.equal(byCca3(c.cca3)?.slug, c.slug);
  }
});

test("every border code is surfaced, resolvable or not — never silently dropped", () => {
  for (const c of countries) {
    const n = neighbours(c);
    assert.equal(n.length, c.borders.length, `${c.slug} lost a border`);
    assert.deepEqual(
      n.map((x) => x.code),
      c.borders,
    );
    // A resolved neighbour must be linkable by slug.
    for (const { country } of n) {
      if (country) assert.ok(bySlug(country.slug));
    }
  }
});

test("regions are the filter options the list page offers", () => {
  assert.ok(regions.length > 1);
  for (const c of countries) assert.ok(regions.includes(c.region));
});
