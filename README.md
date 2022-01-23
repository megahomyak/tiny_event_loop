# TINY EVENT LOOP

An explanation of this implementation of an event loop:

**STEP 1:** Generators in Python can pause themselves when they `yield` a value

**STEP 2:** Make a list of generators and poll them repeatedly

**STEP 3:**
* If you got a new generator, add it to loop and mark current generator
  as its caller, so it can be re-invoked later when the new generator
  runs out.
* If you got an exception, it may be that the generator returned a value or an
  exception, either way you pass it to the caller.
* If you got nothing (None), it means that the current generator wants to return
  control back to the event loop, so we just need to go to the next generator in
  the loop.

**JANUARY 22, 2021**

**THE SHITTY EVENT LOOP INCIDENT**
