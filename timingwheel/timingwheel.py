from time import time


class BaseWheel(object):
    """
    Base implementation of a timing wheel. In fact, noone forces you to even
    use time here.
    """

    def __init__(self, slots, initial_slot=0):
        """
        :type slots: int
        :param slots: how many slots the wheel will have. Keep in mind that the
                      furthest slot you can add to is less by one.
        :type initial_slot: int
        :param initial_slot: the index of a starting slot. Notice that it will
                             be fitted into the size of the wheel by ignoring
                             all full circles.
        """
        self.slots = [{} for _ in xrange(slots)]
        self.position = initial_slot % slots

    def _next_step(self, slots=1):
        """
        Will return the index of the Nth following slot.

        :type slots: int
        :param slots: the offset. Default: 1 (so, the index of the very next
                      slot will be returned)
        """
        return (self.position + slots) % len(self.slots)

    def add(self, key, callback, *args, **kwargs):
        """
        Add an observed item to the last slot (counting from the current one).

        :param key: any hashable object, that will be used as the key.
                    Needs to be unique.
        :param callback: a callable object that will be invoked upon
                         expiration; args and kwargs will be passed to it.
        """
        self.insert(key, len(self.slots) - 1, callback, *args, **kwargs)

    def insert(self, key, slot_offset, callback, *args, **kwargs):
        """
        Add an observed item to Nth slot (counting from the current one).

        :param key: any hashable object, that will be used as the key.
                    Needs to be unique.
        :type slot_offset: int
        :param slot_offset: specifies which slot, starting with the current
                            one, will be used.
        :param callback: a callable object that will be invoked upon
                         expiration; args and kwargs will be passed to it.

        :raises ValueError: when the provided offset is larger than the size
                            of the wheel.
        """
        if slot_offset <= 0:
            raise ValueError(
                'Can\'t insert entries in the past.'
            )

        if slot_offset >= len(self.slots):
            raise ValueError(
                'Cannot add to the {}(st/nd/rd/th) following slot because '
                'there are only {} slots available.'
                .format(slot_offset, len(self.slots))
            )
        slot = self._next_step(slot_offset)
        self.slots[slot][key] = (callback, args, kwargs)

    def remove(self, key):
        """
        Removes the entry, associated with the key, from the wheel.

        :param key: a hashable object, that was previously added/inserted
                    into the wheel.

        :raises KeyError: when there's no entry with that key.
        """
        for offset in xrange(0, len(self.slots)):
            slot = self._next_step(offset)
            if key in self.slots[slot]:
                self.slots[slot].pop(key)
                return

        raise KeyError('Key {} was not found in the wheel.'.format(key))

    def turn(self, slots=1):
        """
        Turns the wheel some steps forward. This will result in expiration
        of any entries that are located in passed slots, starting with the
        current one. The callbacks will be called here.

        :type slots: int
        :param slots: specifies how many slots will be passed. Default: 1.
                      Has to be a non-negative number.

        :raises ValueError: if the requested number of slots is negative.
        """
        if slots < 0:
            raise ValueError('Can\'t turn the wheel backward.')

        for _ in xrange(slots):
            self._expire(self.position)
            self.position = self._next_step()

    def _expire(self, slot):
        """
        Cleans the specified slot and callbacks for all its contents.

        :type slot: int
        :param slot: the slot that will be cleaned.
        """
        slot_contents = self.slots[slot]

        for (callback, args, kwargs) in slot_contents.itervalues():
            if callback:
                callback(*args, **kwargs)

        slot_contents.clear()

    def reset(self, new_position):
        """
        Resets the state: purges all the contents and sets the current position
        to the provided value.

        :type new_position: int
        :param new_position: slot index that will be taken as the current one.
        """
        for slot in self.slots:
            slot.clear()

        self.position = new_position % len(self.slots)


class TimingWheel(BaseWheel):
    """
    A Timing Wheel -- structure that uses time as a force that turns it.
    This particular implementation uses time.time() as the source of time
    and creates slot for every second. It's still your job to give it a turn
    by calling turn() every new second.
    Also, if you desire to change the discretization or use your own source
    of time -- you can simply redefine get_step().
    """

    def __init__(self, step, slots):
        """
        :type step: float
        :param step: the period of time (in seconds) that occupies one slot
        :type slots: int
        :param slots: how many slots the wheel will have. Keep in mind that the
                      furthest slot you can add to is less by one.
        """
        self.step = step
        self.current_step = self.get_step()
        super(TimingWheel, self).__init__(slots, self.current_step)

    def get_step(self):
        """
        The result of this function is used by the class to figure out what
        time is it. Has to return a whole non-negative number.
        """
        return int(time() / self.step)

    def turn(self):
        """
        Calling this method makes the wheel to figure out if it needs to turn
        and turn, if if needs to. It will panic if it finds out that clock
        tuned backwards.

        :raises ValueError: if time that passed since last check is negative.
        """
        new_steps = self.get_step()
        delta = new_steps - self.current_step

        if delta < 0:
            raise ValueError(
                'Time went backwards! Last turn time: {}, current time: {}'
                .format(self.current_step * self.step, new_steps * self.step)
            )

        if delta > 0:
            self.current_step = new_steps
            super(TimingWheel, self).turn(delta)
