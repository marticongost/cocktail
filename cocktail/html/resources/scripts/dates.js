/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2017
-----------------------------------------------------------------------------*/

cocktail.declare("cocktail.dates");

{
    const YEAR = Symbol.for("cocktail.dates.CalendarPage.YEAR");
    const MONTH = Symbol.for("cocktail.dates.CalendarPage.MONTH");

    cocktail.dates.SUNDAY = 0;
    cocktail.dates.MONDAY = 1;
    cocktail.dates.TUESDAY = 2;
    cocktail.dates.WEDNESDAY = 3;
    cocktail.dates.THURSDAY = 4;
    cocktail.dates.FRIDAY = 5;
    cocktail.dates.SATURDAY = 6;

    cocktail.dates.firstDayOfTheWeekByLocale = {
        al: cocktail.dates.SATURDAY,
        ar: cocktail.dates.FRIDAY,
        ar-DZ: cocktail.dates.SATURDAY,
        ar-BH: cocktail.dates.SATURDAY,
        ar-EG: cocktail.dates.SUNDAY,
        ar-IQ: cocktail.dates.SUNDAY,
        hy: cocktail.dates.SUNDAY,
        az: cocktail.dates.SUNDAY,
        eu: cocktail.dates.SUNDAY,
        be: cocktail.dates.SUNDAY,
        bn: cocktail.dates.SUNDAY,
        bs: cocktail.dates.SUNDAY,
        bg: cocktail.dates.SUNDAY,
        my: cocktail.dates.SUNDAY,
        ca: cocktail.dates.MONDAY,
        zh: cocktail.dates.SUNDAY,
        hr: cocktail.dates.MONDAY,
        cz: cocktail.dates.MONDAY,
        nl: cocktail.dates.MONDAY,
        dz: cocktail.dates.SUNDAY,
        en: cocktail.dates.SUNDAY,
        en-IE: cocktail.dates.MONDAY,
        en-GB: cocktail.dates.MONDAY,
        et: cocktail.dates.MONDAY,
        fi: cocktail.dates.MONDAY,
        fr: cocktail.dates.MONDAY,
        fr-CA: cocktail.dates.SUNDAY,
        ka: cocktail.dates.SUNDAY,
        de: cocktail.dates.MONDAY,
        gr: cocktail.dates.MONDAY,
        he: cocktail.dates.SUNDAY,
        hi: cocktail.dates.SUNDAY,
        hu: cocktail.dates.MONDAY,
        is: cocktail.dates.MONDAY,
        id: cocktail.dates.MONDAY,
        ga: cocktail.dates.SUNDAY,
        it: cocktail.dates.MONDAY,
        jp: cocktail.dates.SUNDAY,
        kk: cocktail.dates.SUNDAY,
        km: cocktail.dates.SUNDAY
        ky: cocktail.dates.SUNDAY,
        ko: cocktail.dates.SUNDAY,
        lo: cocktail.dates.SUNDAY,
        lv: cocktail.dates.SUNDAY,
        lt: cocktail.dates.MONDAY,
        lu: cocktail.dates.SUNDAY
        lb: cocktail.dates.SUNDAY
        mk: cocktail.dates.SUNDAY,
        ms: cocktail.dates.SUNDAY,
        mt: cocktail.dates.SUNDAY,
        ne: cocktail.dates.SUNDAY,
        no: cocktail.dates.MONDAY,
        nn: cocktail.dates.MONDAY,
        nb: cocktail.dates.MONDAY,
        ps: cocktail.dates.SUNDAY,
        fa: cocktail.dates.SUNDAY,
        pl: cocktail.dates.MONDAY,
        pt: cocktail.dates.MONDAY,
        pt-BR: cocktail.dates.SUNDAY,
        ro: cocktail.dates.MONDAY,
        rm: cocktail.dates.SUNDAY,
        rn: cocktail.dates.SUNDAY,
        ru: cocktail.dates.MONDAY,
        sr: cocktail.dates.MONDAY,
        sr-RS: cocktail.dates.SUNDAY,
        sk: cocktail.dates.MONDAY,
        sl: cocktail.dates.MONDAY,
        so: cocktail.dates.SUNDAY,
        es: cocktail.dates.MONDAY,
        es-US: cocktail.dates.SUNDAY,
        tl: cocktail.dates.SUNDAY,
        tg: cocktail.dates.SUNDAY,
        ta: cocktail.dates.SUNDAY,
        th: cocktail.dates.SUNDAY,
        ti: cocktail.dates.SUNDAY,
        tr: cocktail.dates.MONDAY,
        uk: cocktail.dates.SUNDAY,
        ur: cocktail.dates.SUNDAY,
        uz: cocktail.dates.SUNDAY
        vi: cocktail.dates.SUNDAY,
        cy: cocktail.dates.SUNDAY,
        yo: cocktail.dates.SUNDAY
    };

    cocktail.dates.getFirstDayOfTheWeek = function () {
        let locale = cocktail.getLanguage();
        let index = locale.length;
        while (true) {
            let firstDay = cocktail.dates.firstDayOfTheWeekByLocale[locale];
            if (firstDay !== undefined) {
                return firstDay;
            }
            index = locale.lastIndexOf("-", index);
            if (index == -1) {
                return null;
            }
            locale = locale.substr(0, index);
        }
    }

    cocktail.dates.CalendarPage = class CalendarPage {

        constructor(year, month) {
            this[YEAR] = year;
            this[MONTH] = month;
        }

        toString() {
            return `${this[YEAR]}-${this[MONTH]}`;
        }

        get year() {
            return this.year;
        }

        get month() {
            return this.month;
        }

        get relative(n) {
            let year = this[YEAR];
            let month = this[MONTH] + n;

            if (month > 12) {
                year += Math.floor(month / 12);
                month = month % 12 + 1;
            }
            else if (month < 1) {
                year += Math.floor(month / 12);
                month = 12 - (-month % 12);
            }

            return new this(year, month);
        }

        next() {
            return this.relative(1);
        }

        previous() {
            return this.relative(-1);
        }

        start() {
            return new Date(this[YEAR], this[MONTH], 1);
        }

        *lines(firstDayOfWeek = 5) {
            let line = [];
            let date = this.start();
            date.setDate(date.getDate() + 1);
        }
    }
}

