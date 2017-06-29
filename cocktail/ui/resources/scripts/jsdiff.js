/*
 * Javascript Diff Algorithm
 *  By John Resig (http://ejohn.org/)
 *  Modified by Chu Alan "sprite"
 *
 * Released under the MIT license.
 *
 * More Info:
 *  http://ejohn.org/projects/javascript-diff-algorithm/
 */

{
    let escape = (s) => {
        let n = s;
        n = n.replace(/&/g, "&amp;");
        n = n.replace(/</g, "&lt;");
        n = n.replace(/>/g, "&gt;");
        n = n.replace(/"/g, "&quot;");
        return n;
    }

    let diff = (o, n) => {

        let ns = {};
        let os = {};

        for (let i = 0; i < n.length; i++) {
            if (ns[n[i]] == null) {
                ns[n[i]] = {rows: [], o: null};
            }
            ns[n[i]].rows.push(i);
        }

        for (let i = 0; i < o.length; i++) {
            if (os[o[i]] == null) {
                os[o[i]] = {rows: [], n: null};
            }
            os[o[i]].rows.push(i);
        }

        for (let i in ns) {
            if (ns[i].rows.length == 1 && typeof(os[i]) != "undefined" && os[i].rows.length == 1) {
                n[ns[i].rows[0]] = {text: n[ns[i].rows[0]], row: os[i].rows[0]};
                o[os[i].rows[0]] = {text: o[os[i].rows[0]], row: ns[i].rows[0]};
            }
        }

        for (let i = 0; i < n.length - 1; i++) {
            if (
                n[i].text != null
                && n[i+1].text == null
                && n[i].row + 1 < o.length
                && o[n[i].row + 1].text == null
                && n[i+1] == o[n[i].row + 1]
            ) {
                n[i+1] = {text: n[i+1], row: n[i].row + 1};
                o[n[i].row+1] = {text: o[n[i].row+1], row: i + 1};
            }
        }

        for (let i = n.length - 1; i > 0; i--) {
            if (
                n[i].text != null
                && n[i-1].text == null
                && n[i].row > 0
                && o[n[i].row - 1].text == null
                && n[i-1] == o[n[i].row - 1]
            ) {
                n[i-1] = {text: n[i-1], row: n[i].row - 1};
                o[n[i].row-1] = {text: o[n[i].row-1], row: i - 1};
            }
        }

        return {o, n};
    }

    cocktail.ui.diffString = (o, n) => {

        o = o.replace(/\s+$/, '');
        n = n.replace(/\s+$/, '');

        let out = diff(o == "" ? [] : o.split(/\s+/), n == "" ? [] : n.split(/\s+/));
        let str = "";

        let oSpace = o.match(/\s+/g);
        if (oSpace == null) {
            oSpace = ["\n"];
        } else {
            oSpace.push("\n");
        }

        let nSpace = n.match(/\s+/g);
        if (nSpace == null) {
            nSpace = ["\n"];
        }
        else {
            nSpace.push("\n");
        }

        if (out.n.length == 0) {
            for (let i = 0; i < out.o.length; i++) {
                str += '<del>' + escape(out.o[i]) + oSpace[i] + "</del>";
            }
        }
        else {
            if (out.n[0].text == null) {
                for (n = 0; n < out.o.length && out.o[n].text == null; n++) {
                    str += '<del>' + escape(out.o[n]) + oSpace[n] + "</del>";
                }
            }

            for (let i = 0; i < out.n.length; i++ ) {
                if (out.n[i].text == null) {
                    str += '<ins>' + escape(out.n[i]) + nSpace[i] + "</ins>";
                }
                else {
                    let pre = "";
                    for (n = out.n[i].row + 1; n < out.o.length && out.o[n].text == null; n++) {
                        pre += '<del>' + escape(out.o[n]) + oSpace[n] + "</del>";
                    }
                    str += " " + out.n[i].text + nSpace[i] + pre;
                }
            }
        }

        return str;
    }
}

