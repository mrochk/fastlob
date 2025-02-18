- [ ] testing for market orders placing if not filled 
- [ ] testing for FOK orders
- [ ] testing for GTC orders
- [ ] testing for GTD orders
- [ ] testing for order cancellation 
- [ ] multi-threading (methods thats affect the state of the book separated from methods that concern the user)
- [ ] user should be able to control number of limits displayed
- [x] Limits do not need to have a side attribute
- [x] limits may be printed differently
- [x] orderbook and side should have a proper __repr__ and a view() method

***

- [ ] ob result and order params may be moved to separate packages (?)
- [ ] is there something faster than `decimal` ?