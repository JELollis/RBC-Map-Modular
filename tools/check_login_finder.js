// Execute the app's generated finder against synthetic pages.
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { Script } = require("node:vm");

const finder = new Script(readFileSync(0, "utf8"), { filename: "LOGIN_FORM_FINDER_JS" });
const gameOrigin = "https://quiz.ravenblack.net";

function check(label, fieldNames, expected, origin = gameOrigin) {
    const forms = fieldNames.map((names) => {
        const fields = new Map(names.map((name) => [`input[name="${name}"]`, { name }]));
        return { querySelector: (selector) => fields.get(selector) ?? null };
    });
    const document = {
        querySelectorAll(selector) {
            assert.equal(selector, "form");
            return forms;
        },
    };
    const result = finder.runInNewContext({ document, location: { origin } });
    if (expected === null) {
        assert.equal(result, null, label);
        return;
    }

    const [formIndex, userName, passName] = expected;
    assert.ok(result, label);
    assert.equal(result.form, forms[formIndex], label);
    assert.equal(result.user?.name, userName, label);
    assert.equal(result.pass?.name, passName, label);
}

check("creation form before the live login", [["iam"], ["iam", "passwd"]], [1, "iam", "passwd"]);
check("alternate login", [["username", "password"]], [0, "username", "password"]);
check("split fields", [["iam"], ["passwd"]], null);
check("creation form alone", [["iam"]], null);
check("password-change form", [["password", "confirm"]], null);
check("mixed field pairs", [["iam", "password"]], null);
check("wrong origin", [["iam", "passwd"]], null, "https://example.invalid");

console.log("login finder behavior checks passed");
