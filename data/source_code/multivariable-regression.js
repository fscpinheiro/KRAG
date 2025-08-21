module.exports = class multivariateRegression {
    //TREINO
    train(config={}) {
        this._config = {};

        if(config.input) {
            const tempX = config.input;
            let concatX = [];
            for(let i=0; i<tempX.length; i++){
                const temp = tempX[i].reduce((a, b) => a+''+b);
                concatX.push(Number(temp));
            }
            this.X = concatX;
        } else { 
            this.X = [[0,0]]; 
        }

        if(config.output) this.Y = config.output; else this.Y = [0];
        
        this._config.input = this.X;
        this._config.output = this.Y;
    }

    //SALVAR TREINO
    saveModel(path='./model.json'){
        const fs = require('fs');
        fs.writeFileSync(path, JSON.stringify(this._config));
    }

    //LOAD MODEL
    loadModel(path='./model.json'){
        const fs = require('fs');
        const data = fs.readFileSync(path, 'utf8');
        const json = JSON.parse(data);
        this.X = json.input;
        this.Y = json.output;
    }

    //CALCULO DOS PRODUTOS DE X, Y
    produto(x,y){
        let temp = [];
        for(let i=0; i<x.length; i++)
            temp.push(parseFloat(x[i]) * parseFloat(y[i]));
        return temp;
    }

    //CALCULO DOS QUADRADOS DE X
    quadrados(x){
        let temp = [];
        for(let i=0; i<x.length; i++)
            temp.push(parseFloat(x[i]) * parseFloat(x[i]));
        return temp;
    }

    //CALCULO DO SOMATORIO
    somatorio(x=[]){
        let soma = 0;
        for(let i=0; i<x.length; i++){
            soma = soma + parseFloat(x[i]);        
        }
        return parseFloat(soma);
    }

    //CALCULO DA MÉDIA
    media(x=[]){
        return this.somatorio(x) / x.length;
    }

    //RESULTADOS PARA REGRESSÃO LINEAR
    resultados(x=[], y=[], p=0){
        const resultado1 = (this.somatorio(x) * this.somatorio(y)) / x.length;
        const resultado2 = (this.somatorio(x) * this.somatorio(x)) / x.length;
        const resultado3 = this.somatorio(this.produto(x, y)) - resultado1;
        const resultado4 = resultado3 / (this.somatorio(this.quadrados(x)) - resultado2);
        const resultado5 = this.media(y) - (resultado4 * this.media(x));
        
        return ((resultado4 * p) + resultado5).toFixed(0);
    }

    //PREDICT
    predict(p=[]){        
        const tempX = p;
        let concatX = [];
        for(let i=0; i<tempX.length; i++){
            const temp = tempX[i].reduce((a, b) => a+''+b);
            concatX.push(Number(temp));
        }
        p = concatX;
        let regressoes = [];
        for(let i=0; i<p.length; i++){
            const temp = Number(this.resultados(this.X, this.Y, p[i]));
            regressoes.push(temp);
        }
        return regressoes;        
    }
}