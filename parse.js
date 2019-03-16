const d3 = require("d3");

if (typeof fetch !== 'function') {
    global.fetch = require('node-fetch-polyfill');
}
const csv = require('d3-fetch').csv;



//Declare variables
let activityTotal = {};
let activityArray = [];
let newArray = [];
let timechunk;
let result;
let max;
let citiDateFix;
let transactions;
let singleDayFiltered;
let timeChunkArray = [];
let sleepChunkArray = [];
let deepChunkArray = [];
let dayChoice = "2017-05-10";



function citiParse(citiData){
  let citiDateFix = citiData.map(currentRow => {
    let oldDate = currentRow['Date'].split("/");
    let newDate = oldDate[2] + "-" + oldDate[0] + "-" + oldDate[1];
    currentRow['Date'] = newDate;
    return currentRow;

  })
  transactions = citiDateFix.filter(row => (row['Date'].includes(dayChoice)));
  console.log(transactions);

  let transactionMax = d3.max(transactions, function(d) { return +d['Debit']} );

  console.log(transactionMax);

}

//This function parses RescueTime data

function rescueTimeParse(activityData){

  //Using the dayChoice variable we filter out only the rows that pertain to that day
  singleDayFiltered = activityData.filter(activity => (activity[Object.keys(activity)[1]].includes(dayChoice)));


  //Here we fill in empty cells with zeroes
  let activityCount = singleDayFiltered.map(currentRow => {
    if (typeof(activityTotal[Object.values(currentRow)[2]]) != "number"){
      activityTotal[Object.values(currentRow)[2]] = 0
    };

    //this part builds and objects where each key is an activity and tallies up the values for each over the entire day
    activityTotal[Object.values(currentRow)[2]] = parseInt(activityTotal[Object.values(currentRow)[2]]) + parseInt(Object.values(currentRow)[0]);

    newArray.push({
      "name" : Object.values(currentRow)[2],
      "amount" : parseInt(activityTotal[Object.values(currentRow)[2]]) + parseInt(Object.values(currentRow)[0]),
      "category" : Object.values(currentRow)[4]
    })
  }, 0);

    activityArray = Object.entries(activityTotal);

    activityArray.sort(function(x, y){
   return d3.ascending(x[1], y[1]);
    })
    let max = d3.max(activityArray, function(d) { return +d[1]} );

    activityDraw(max)

};


  //here we're converting Google Fit timestamps into milliseconds
function timestampMilliConverter(entry){
    timechunk = entry[ 'Start time' ].slice(0,5);
    timechunk = (Number(timechunk.split(':')[0])*60+Number(timechunk.split(':')[1]))*1000;
    timeChunkArray.push(timechunk)
    return;
  };


//This function parses Google Fit data (sleep, deep sleep, step count)
function fitParse(data) {
  //here we're iterating over each row and converting the values to integers
  //where the value is non-existant we mark it zero
    data.forEach(function(row){
      if (row[ 'Sleep duration (ms)' ] > 0){
        row[ 'Sleep duration (ms)' ] = parseInt(row[ 'Sleep duration (ms)' ])
      } else row[ 'Sleep duration (ms)' ] = 0;
      if (row[ 'Deep sleeping duration (ms)' ] > 0){
        row[ 'Deep sleeping duration (ms)' ] = parseInt(row[ 'Deep sleeping duration (ms)' ])
      } else row[ 'Deep sleeping duration (ms)' ] = 0;
      if (row[ 'Step count' ] > 0){
        row[ 'Step count' ] = parseInt(row[ 'Step count' ])
      } else row[ 'Step count' ] = 0;
    });

    //here we use reduce functions to tally up the amount of each
      const lightCount = data.reduce((total, chunk) => {
        sleepChunkArray.push(chunk[ 'Sleep duration (ms)' ]);
        return total + chunk[ 'Sleep duration (ms)' ];
      }, 0);
      const deepCount = data.reduce((total, chunk) => {
        deepChunkArray.push(chunk[ 'Deep sleeping duration (ms)' ]);
        return total + chunk[ 'Deep sleeping duration (ms)' ];
      }, 0);
      const stepCount = data.reduce((total, chunk) => {
        return total + chunk[ 'Step count' ];
      }, 0);

      //adding up the total count
      const sleepCount = lightCount + deepCount;
      const sleepCountArray = [sleepCount, 86400000];


      const test = data.forEach((chunk) => {
        timestampMilliConverter(chunk)
      });

  };

  d3.csv("test_data/" + dayChoice + ".csv", function(fitData){
      fitParse(fitData);
    });

  d3.csv("test_data/rescuetime-activity-history.csv", function(rescueTimeData){
      rescueTimeParse(rescueTimeData);
    });

  d3.csv("test_data/Citi.csv", function(citiData){
      citiParse(citiData);
    });
