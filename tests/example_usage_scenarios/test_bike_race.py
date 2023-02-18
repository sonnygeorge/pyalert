from typing import List

import pytest

from pyalert import PyAlerts, pyalert, alert_conf

SUSPICIOUSLY_FAST_AVG_MPH = 40
IMPOSSIBLY_FAST_AVG_MPH = 70
CURRENT_RECORD_AVG_MPH = 46
VERBOSE_ANNOUNCEMENT_LENGTH = 100
SUSPICIOUSLY_FAST_MSG = "Suspiciously fast biker(s) found: {bikers}... Drug test time!"
IMPOSSIBLY_FAST_MSG = (
    "Impossibly fast biker(s) found: {bikers}... Check speedometer calibration!"
)
RECORD_BROKEN_MSG = "New records speeds achieved: {bikers}"
BAD_RACE_MSG = "Bad race! Reasons: {reasons}"
ALL_MPH_NEG_MSG = "All bikers mph are negative!"
NO_NAMES_MSG = "No names found for bikers!"
ALL_AGES_NEG_MSG = "All bikers ages are invalid!"
VERBOSE_ANNOUNCEMENT_MSG = "Verbose announcement: {announcement:.150}..."
ANNOUNCEMENT = (
    "What a race! The winner was {winner} with an average speed of {mph} mph!"
)


class BikeRaceAlerts(PyAlerts):
    """Alerts for bike_race"""

    @alert_conf(takes="input", raise_error=False)
    def suspiciously_fast_bikers(self, *args, **kwargs):
        """Alerts which bikers are suspiciously fast"""
        bikers = args[0] if args else kwargs["bikers"]
        suspiciously_fast_bikers = [
            f"{b.name}: {b.avg_mph} mph"
            for b in bikers
            if b.avg_mph > SUSPICIOUSLY_FAST_AVG_MPH
        ]
        assert (
            not suspiciously_fast_bikers
        ), f"Suspiciously fast biker(s) found: {suspiciously_fast_bikers}... Drug test time!"

    @alert_conf(takes="input", raise_error=False)
    def impossibly_fast_bikers(self, *args, **kwargs):
        """Alerts which bikers are impossibly fast"""
        bikers = args[0] if args else kwargs["bikers"]
        impossibly_fast_bikers = [
            f"{b.name}: {b.avg_mph} mph"
            for b in bikers
            if b.avg_mph > IMPOSSIBLY_FAST_AVG_MPH
        ]
        assert not impossibly_fast_bikers, IMPOSSIBLY_FAST_MSG.format(
            bikers=impossibly_fast_bikers
        )

    @alert_conf(takes="input", raise_error=False)
    def record_broken(self, *args, **kwargs):
        """Alerts which bikers have broken the record"""
        bikers = args[0] if args else kwargs["bikers"]
        record_broken_bikers = [
            f"{b.name}: {b.avg_mph} mph"
            for b in bikers
            if b.avg_mph > CURRENT_RECORD_AVG_MPH
        ]
        assert not record_broken_bikers, RECORD_BROKEN_MSG.format(
            bikers=record_broken_bikers
        )

    @alert_conf(takes="input", raise_error=True)
    def bad_race(self, *args, **kwargs):
        """Raises error and alerts on bad race conditions"""
        bikers = args[0] if args else kwargs["bikers"]
        checks = []
        checks.append((lambda bkrs: all(b.avg_mph < 0 for b in bkrs), ALL_MPH_NEG_MSG))
        checks.append((lambda bkrs: all(not b.name for b in bkrs), NO_NAMES_MSG))
        checks.append((lambda bkrs: all([b.age < 0 for b in bkrs]), ALL_AGES_NEG_MSG))
        bad_race_reasons = [msg for check, msg in checks if check(bikers)]
        assert not bad_race_reasons, BAD_RACE_MSG.format(reasons=bad_race_reasons)

    @alert_conf(takes="output", raise_error=False)
    def verbose_announcement(self, return_value):
        """Alerts if announcement is verbose"""
        announcement = return_value
        not_verbose = len(announcement) < VERBOSE_ANNOUNCEMENT_LENGTH
        assert not_verbose, VERBOSE_ANNOUNCEMENT_MSG.format(announcement=announcement)

class Biker:
    def __init__(self, name: str, age: int, avg_mph: int):
        self.name = name
        self.age = age
        self.avg_mph = avg_mph


@pyalert(pyalerts=BikeRaceAlerts)
def bike_race(bikers: List[Biker]) -> str:
    """A simple bike race"""
    winner = max(bikers, key=lambda biker: biker.avg_mph)
    announcement = ANNOUNCEMENT.format(winner=winner.name, mph=winner.avg_mph)
    return announcement


class TestBikeRace:
    _normal_bikers = [
        Biker("Steve", 30, SUSPICIOUSLY_FAST_AVG_MPH - 5),
        Biker("Lisa", 25, SUSPICIOUSLY_FAST_AVG_MPH - 7),
        Biker("Doug", 40, SUSPICIOUSLY_FAST_AVG_MPH - 10),
    ]

    def test_no_alerts_normal_race(self, capsys):
        bike_race(self._normal_bikers)
        assert "PYALERT" not in capsys.readouterr().out

    def test_suspiciously_fast(self, capsys):
        for num_suspicious in range(1, 4):
            bikers = self._normal_bikers.copy()
            for i in range(num_suspicious):
                bikers[i].avg_mph = SUSPICIOUSLY_FAST_AVG_MPH + 1
            suspiciously_fast_bikers = [
                f"{b.name}: {b.avg_mph} mph"
                for b in bikers
                if b.avg_mph > SUSPICIOUSLY_FAST_AVG_MPH
            ]
            bike_race(bikers)
            assert (
                SUSPICIOUSLY_FAST_MSG.format(bikers=suspiciously_fast_bikers)
                in capsys.readouterr().out
            )

    def test_impossibly_fast(self, capsys):
        for num_impossible in range(1, 4):
            bikers = self._normal_bikers.copy()
            for i in range(num_impossible):
                bikers[i].avg_mph = IMPOSSIBLY_FAST_AVG_MPH + 1
            impossibly_fast_bikers = [
                f"{b.name}: {b.avg_mph} mph"
                for b in bikers
                if b.avg_mph > IMPOSSIBLY_FAST_AVG_MPH
            ]
            bike_race(bikers)
            assert (
                IMPOSSIBLY_FAST_MSG.format(bikers=impossibly_fast_bikers)
                in capsys.readouterr().out
            )

    def test_record_broken(self, capsys):
        for num_impossible in range(1, 4):
            bikers = self._normal_bikers.copy()
            for i in range(num_impossible):
                bikers[i].avg_mph = CURRENT_RECORD_AVG_MPH + 1
            record_broken_bikers = [
                f"{b.name}: {b.avg_mph} mph"
                for b in bikers
                if b.avg_mph > CURRENT_RECORD_AVG_MPH
            ]
            bike_race(bikers)
            assert (
                RECORD_BROKEN_MSG.format(bikers=record_broken_bikers)
                in capsys.readouterr().out
            )

    def test_bad_race(self):
        cases = [
            [
                Biker("", -5, -2),
                Biker("", -4, -7),
                Biker("", -3, -5),
            ]
        ]
        for key, bad_data in {"name": "", "age": -1, "avg_mph": -1}.items():
            bikers = self._normal_bikers.copy()
            for biker in bikers:
                setattr(biker, key, bad_data)
            cases.append(bikers)
        for case in cases:
            with pytest.raises(Exception):
                bike_race(case)

    def test_verbose_announcement(self, capsys):
        long_name = "A" * (VERBOSE_ANNOUNCEMENT_LENGTH + 1)
        bikers = [
            Biker("Steve", 30, 28),
            Biker(long_name, 25, 32),
            Biker("Doug", 40, 29),
        ]
        bike_race(bikers)
        winner = max(bikers, key=lambda biker: biker.avg_mph)
        announcement = ANNOUNCEMENT.format(winner=winner.name, mph=winner.avg_mph)
        assert (
            VERBOSE_ANNOUNCEMENT_MSG.format(announcement=announcement)
            in capsys.readouterr().out
        )


if __name__ == "__main__":
    pytest.main()
