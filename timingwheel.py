from time import time


class BaseWheel(object):
    def __init__(self, slots, initial_slot=0, miss_callback=None):
        self.position = initial_slot
        self.slots = [{} for _ in xrange(slots)]
        self.miss_callback = miss_callback

    def _next_step(self, slots=1):
        return (self.position + slots) % len(self.slots)

    def add(self, key, value):
        slot = self._next_step(len(self.slots) - 1)
        self.slots[slot][key] = value

    def remove(self, key):
        for offset in xrange(1, len(self.slots) - 1):
            slot = self._next_step(offset)
            if key in self.slots[slot]:
                self.slots[slot].pop(key)
                return

        raise KeyError('Key {} was not found in the wheel.'.format(key))

    def turn(self, slots=1):
        for _ in xrange(slots):
            self.expire(self.position)
            self.position = self._next_step()

    def expire(self, slot):
        slot_contents = self.slots[slot]

        if self.miss_callback:
            for value in slot_contents.itervalues():
                self.miss_callback(value)

        slot_contents.clear()

    def reset(self, new_position):
        for slot in self.slots:
            slot.clear()
        self.position = new_position


class TimeWheel(BaseWheel):
    def __init__(self, slots, miss_callback=None):
        self.current_time = self.get_time()
        super(TimeWheel, self).__init__(slots, self.current_time % slots, miss_callback)

    def get_time(self):
        return int(time())

    def turn(self):
        new_time = self.get_time()
        delta = new_time - self.current_time

        if delta < 0:
            raise ValueError('Time went backwards! Last turn time: {}, current time: {}'
                             .format(self.current_time, new_time))

        if delta > 0:
            super(TimeWheel, self).turn(delta)
