# Timing Wheel

This library implements the algorithm of managing lots and lots of callbacks that needs to be run at the certain time. It is most useful in the situations when we need to often insert and remove callbacks.

Typical use case is a server that controls a message exchange with a big number of clients; each message that is sent to a client has to be acknowledged and there is a certain timeout that needs to be checked to determine whether the connection still exists.

Timing Wheel has a complexity of O(1) for inserting, deleting and setting an entry to run. That's why it's awesome.

In the nutshell, it is a circular buffer, each slot of which is dedicated to a certain point of time in the future. A cursor, that runs along the buffer, runs all the callbacks that are stored in a slot it passes. If we need to insert a callback, we put it in a slot that is N slots away from the current cursor position.

Keep in mind that it is the simplest possible implementation, and it has certain weak points:
 * You can't insert an entry that needs to be run further away in the future than the size of the wheel. This problem can be solved by adding a structure, that holds all such items and putting them into the wheel when you can.
 * You can't control the order in which the callbacks of a specific time slot will be run. Really, they are stored in a dict to ensure O(1) deletion. Possible solution: put all the entries of the slot that's about to expire into a heap.
 * You can't insert an entry in the slot that is about to expire. Thus, the shortest amount of time between inserting a callback and running it is dt..2*dt, where dt is the step of the wheel.
 * Also, currently there's no way to set the set the step of the TimingWheel class, only its size. The step is set to 1 second.

That's it, if you have any questions, please mail me at iljich@iljich.name
