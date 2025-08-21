const multivariateRegression = require('./multivariable-regression');

const config = {
    input: [[1,2], [2,3], [3,4], [4,5]],
    output: [3,5,7,9]
};

const regression = new multivariateRegression();
regression.train(config);

const result = regression.predict([[5,6], [6,7]]);
console.log(result);