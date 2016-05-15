import pytest

from timingwheel import BaseWheel, TimeWheel


class TestBaseWheel(object):
    @pytest.fixture()
    def wheel(self):
        return BaseWheel(10, 5)

    def test_inst(self, wheel):
        assert len(wheel.slots) == 10
        assert wheel.position == 5

    def test_next_step(self, wheel):
        assert wheel._next_step() == 6
        assert wheel._next_step(2) == 7
        assert wheel._next_step(10) == 5
        assert wheel._next_step(100) == 5

    def test_add(self, wheel):
        key, callback, args, kwargs = \
            object(), object(), (object(),), {'a': object()}
        wheel.add(key, callback, *args, **kwargs)

        assert wheel.slots[4] == {
            key: (callback, args, kwargs)
        }

    def test_insert_ok(self, wheel):
        key, callback, args, kwargs = \
            object(), object(), (object(),), {'a': object()}
        wheel.insert(key, 1, callback, *args, **kwargs)

        assert wheel.slots[6] == {
            key: (callback, args, kwargs)
        }

    def test_insert_too_large(self, wheel):
        key, callback, args, kwargs = \
            object(), object(), (object(),), {'a': object()}

        with pytest.raises(ValueError):
            wheel.insert(key, 100, callback, *args, **kwargs)

    def test_insert_too_little(self, wheel):
        key, callback, args, kwargs = \
            object(), object(), (object(),), {'a': object()}

        with pytest.raises(ValueError):
            wheel.insert(key, 0, callback, *args, **kwargs)

        with pytest.raises(ValueError):
            wheel.insert(key, -10, callback, *args, **kwargs)

    def test_remove_ok(self, wheel):
        key, callback, args, kwargs = \
            object(), object(), (object(),), {'a': object()}

        wheel.add(key, callback, *args, **kwargs)
        wheel.remove(key)

        assert wheel.slots == [{}] * 10

    def test_remove_no_such_key(self, wheel):
        key = object()
        with pytest.raises(KeyError):
            wheel.remove(key)

    def test_turn_empty(self, wheel):
        wheel.turn()
        assert wheel.position == 6

        wheel.turn(2)
        assert wheel.position == 8

        wheel.turn(10)
        assert wheel.position == 8

        wheel.turn(100)
        assert wheel.position == 8

    def test_turn_ok(self, wheel):
        called = []

        def callback(index):
            called.append(index)

        for index in xrange(1, 10):
            wheel.insert(
                key=index, slot_offset=index, callback=callback, index=index
            )

        wheel.turn()
        assert called == []

        wheel.turn()
        assert called == [1]

        wheel.turn(5)
        assert called == [1, 2, 3, 4, 5, 6]

        wheel.turn(50)
        assert called == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_turn_backwards(self, wheel):
        with pytest.raises(ValueError):
            wheel.turn(-10)

    def test_reset(self, wheel):
        for index in xrange(1, 10):
            wheel.insert(key=object(), slot_offset=index, callback=object())

        wheel.reset(3)
        assert wheel.position == 3
        assert wheel.slots == [{}] * 10


class TestTimingWheel(object):
    time = 1000

    @pytest.fixture(autouse=True)
    def fixed_time(self, set_clock):
        set_clock(self.time)

    @pytest.fixture()
    def wheel(self):
        return TimeWheel(10)

    @pytest.fixture()
    def set_clock(self, monkeypatch):
        def inner(time):
            monkeypatch.setattr('timingwheel.time', lambda: time)
        return inner

    def test_inst(self, wheel):
        assert wheel.current_time == self.time
        assert wheel.position == 0

    def test_get_time(self, wheel, set_clock):
        set_clock(1000.5)
        assert wheel.get_time() == 1000

        set_clock(1001.5)
        assert wheel.get_time() == 1001

    def test_turn_empty(self, wheel, set_clock):
        set_clock(1000.5)
        wheel.turn()
        assert wheel.position == 0
        assert wheel.current_time == 1000

        set_clock(1001)
        wheel.turn()
        assert wheel.position == 1
        assert wheel.current_time == 1001

        set_clock(1020)
        wheel.turn()
        assert wheel.position == 0
        assert wheel.current_time == 1020

    def test_turn_ok(self, wheel, set_clock):
        called = []

        def callback(index):
            called.append(index)

        for index in xrange(1, 10):
            wheel.insert(
                key=index, slot_offset=index, callback=callback, index=index
            )

        set_clock(1001)
        wheel.turn()
        assert called == []

        set_clock(1002)
        wheel.turn()
        assert called == [1]

        set_clock(1007)
        wheel.turn()
        assert called == [1, 2, 3, 4, 5, 6]

        set_clock(1100)
        wheel.turn()
        assert called == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_turn_backwards(self, wheel, set_clock):
        set_clock(900)
        with pytest.raises(ValueError):
            wheel.turn()
