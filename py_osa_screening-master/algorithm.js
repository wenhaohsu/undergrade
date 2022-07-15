var Decimal = require('decimal.js');
var ss = require('simple-statistics');

Decimal.set({ precision: 3 });

function diff(array) {
    var new_array = [];
    for (var i = 0; i < array.length-1; i++) {
        new_array.push(array[i+1] - array[i]);
    }
    return new_array;
}

function exportJson(data,ODI,AHI,SPO2_event) {
    var export_data = {
        'report': {
            filename: '',
            baseline: ss.mode(data.SPO2),
            mean: Number(new Decimal(ss.mean(data.SPO2)).round().valueOf()),
            lowest: ss.min(data.SPO2),
            total_time: Number(new Decimal(data.Time.length).valueOf()), //sec
            de_oxygen: Number(ODI.valueOf()),
            esti_AHI: Number(AHI.valueOf())                
        },
        'event': SPO2_event
    };
    return export_data;
}

module.exports = function AHIAlgorithm(data) {
    var SPO2 = [];
    var SPO2_origin_location = []; // 紀錄原始血氧訊號位置 (除噪後)
    var SPO2_mark_location = []; // 紀錄原始血氧訊號標記 (除噪後)
    var Threshold = 3; // 血氧閾值
    var DurationTime = 75; // 血氧事件持續時間最大值
    var Activity = 2; // 活動量閾值

    var TimeInBed = data.raw_SPO2.length; // 估計躺床時間
    console.time('Algorithm Time');
    for (var i = 0; i < data.raw_SPO2.length; i++) { // 過濾掉極端值
        if (data.raw_SPO2[i] == 0 || data.raw_SPO2[i] == -1 || data.raw_SPO2[i] > 100 || data.raw_SPO2[i] < 70  ||  data.PA[i] > Activity ) {
            TimeInBed--;
            continue;
        }
        // if (data.PA[i] > Activity)
        //     TimeInBed--;
        SPO2.push(data.raw_SPO2[i]);
        SPO2_origin_location.push(i);
    }
    console.log("TimeInBed",TimeInBed);
    if (SPO2.length == 0) {
        return 0;
    }
    data['SPO2'] = SPO2;
    var ISPO2 = diff(SPO2); // 計算前後差異
    var NPSPO2 = [], Realindex = [];
    for (var i = 0; i < ISPO2.length; i++) {
        if (ISPO2[i] != 0) {
            NPSPO2.push(SPO2[i+1]); // 有變化波段的值
            Realindex.push(i+1); // 有變化波段在SPO2實際的位置
        }
    }
    var NPNPSPO2 = diff(NPSPO2);
    var IndMin = [], IndMax = [];
    for (var i = 0; i < NPNPSPO2.length-1; i++) {
        var temp = Math.sign(NPNPSPO2[i+1]) - Math.sign(NPNPSPO2[i]);
        if (temp > 0)
            IndMin.push(i+1); // 波谷位置
        else if (temp < 0)
            IndMax.push(i+1); // 波峰位置
    }
    var peak_values = [], peak_values_index = [], trough_values = [], trough_values_index = [];

    for (var i = 0; i < IndMax.length; i++) {
        peak_values.push(NPSPO2[IndMax[i]]); // 波峰值
        peak_values_index.push(Realindex[IndMax[i]]); // 波峰在SPO2實際的位置       
        SPO2_mark_location[Realindex[IndMax[i]]] = 'peak,' + SPO2_origin_location[Realindex[IndMax[i]]] + ',' + NPSPO2[IndMax[i]]; // 波峰在SPO2_origin實際的位置       
    }

    for (var i = 0; i < IndMin.length; i++) {
        trough_values.push(NPSPO2[IndMin[i]]); // 波谷值
        trough_values_index.push(Realindex[IndMin[i]]); // 波谷在SPO2實際的位置       
        SPO2_mark_location[Realindex[IndMin[i]]] = 'trough,' + SPO2_origin_location[Realindex[IndMin[i]]] + ',' + NPSPO2[IndMin[i]]; // 波谷在SPO2_origin實際的位置       
    }

    // 判斷先有波峰還是波谷
    var peak_count = peak_values.length;
    var trough_count = trough_values.length;
    var count_diff = Math.abs(peak_count - trough_count);
    // console.log("NPNPSPO2[0] > 0: ",(NPNPSPO2[0] > 0),'count_diff: ',count_diff);
    SPO2_mark_location = SPO2_mark_location.filter(function(n){ return n != undefined }); // 整理 SPO2_mark_location
    // console.log(SPO2_mark_location);
    // 整理為相同個數
    if (NPNPSPO2[0] > 0) { // 先有波峰
        if (count_diff == 1) {
            peak_values.pop();
            peak_values_index.pop();
            SPO2_mark_location.pop();
        }
    }
    else {
        if (count_diff == 1) {
            trough_values = trough_values.slice(1);
            trough_values_index = trough_values_index.slice(1);
            SPO2_mark_location = SPO2_mark_location.slice(1);
        }
        else {
            peak_values.pop();
            peak_values_index.pop();
            trough_values = trough_values.slice(1);
            trough_values_index = trough_values_index.slice(1);
            SPO2_mark_location.pop();
            SPO2_mark_location = SPO2_mark_location.slice(1);         
        }
    }
    var amp = [], duration = [];
    var O2_DELTA = [], ODI = [], AHI = [], O2_DELTA_4 = [];
    for (var i = 0; i < peak_values.length; i++) {
        if (Math.abs(peak_values_index[i] - trough_values_index[i]) <= DurationTime) {
            amp.push(peak_values[i] - trough_values[i]);
            if (peak_values[i] - trough_values[i] >= Threshold) {
                O2_DELTA.push(peak_values[i] - trough_values[i]);
            }
            if (peak_values[i] - trough_values[i] >= 4) {
                O2_DELTA_4.push(peak_values[i] - trough_values[i]);
            }
        }
    }

    // json
    var SPO2_event = {};
    var SPO2_event_count = 0;
    for (var i = 0; i < SPO2_mark_location.length; i += 2) {
        if (Math.abs(peak_values_index[i/2] - trough_values_index[i/2]) <= DurationTime) {
            if (Number(SPO2_mark_location[i].split(',')[2]) - Number(SPO2_mark_location[i+1].split(',')[2]) >= Threshold) {
                SPO2_event[String(SPO2_event_count)] = {};
                SPO2_event[String(SPO2_event_count)].time = data['Time'][SPO2_mark_location[i].split(',')[1]];
                SPO2_event[String(SPO2_event_count)].duration = Math.abs(Number(SPO2_mark_location[i].split(',')[1]) - Number(SPO2_mark_location[i+1].split(',')[1]));
                // SPO2_event[String(SPO2_event_count)].PA = [];
                // SPO2_event[String(SPO2_event_count)].index = SPO2_mark_location[i];
                // for (var k = 0; k < SPO2_event[String(SPO2_event_count)].duration; k++) {
                //     SPO2_event[String(SPO2_event_count)].PA.push(data['PA'][Number(SPO2_mark_location[i].split(',')[1]) + k]);
                // }
                SPO2_event_count++;
            }
        }
    }
    // console.log(SPO2_event);
    ODI = new Decimal(O2_DELTA.length);
    ODI4 = new Decimal(O2_DELTA_4.length);
    ODI_new = new Decimal(ODI).plus(ODI4);
    ODI_new = ODI_new.div(2);
    AHI = ODI.dividedBy(Decimal.max(1,(new Decimal(TimeInBed).dividedBy(3600))));
    AHI_new = ODI_new.dividedBy(Decimal.max(1,(new Decimal(TimeInBed).dividedBy(3600))));
    console.log("ODI",ODI.valueOf());
    console.log("ODI4",ODI4.valueOf());
    console.log("AHI",AHI.valueOf());
    console.log("AHI_new",AHI_new.valueOf());
    console.timeEnd('Algorithm Time');
    // AHI 為ODI3運算，AHI_new 為ODI3+ODI4平均運算，
    SPO2_event = exportJson(data, ODI, AHI_new, SPO2_event);
    // console.log("TimeInBed", TimeInBed);
    return {
        data: data,
        ODI: ODI,
        AHI: AHI_new,
        event: SPO2_event
    };
}
