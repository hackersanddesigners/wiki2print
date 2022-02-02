"""How to use the 'magicword' API.

In this example, we have a pad called "my-pad-name" on our etherpad-lite
instance. Inside the content of that pad is the so-called "magic word"
__WORSE_IS_BETTER__. The "@magicword" takes care of retrieving all the formats
of those pads and returns a dictionary called "pads" ready to go.

Run this example like so:

$ python etherdump/examples/magicword.py

"""

from etherpump.api import magicword


@magicword('__WORSE_IS_BETTER__')
def can_be_called_anything_you_like(pads):
    print(pads['foobar']['html'])
    print(pads['foobar']['txt'])
    print(pads['foobar']['meta'])


if __name__ == "__main__":
    can_be_called_anything_you_like()
