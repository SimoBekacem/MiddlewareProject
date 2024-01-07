const BIRDS = require('../models/birds.model');

exports.getBirdsList = (req, res) => {
	res.json(BIRDS);
};
