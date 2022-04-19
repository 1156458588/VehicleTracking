import copy

a = [[[[3, 10159, 0.42349496483802795, [10144, 10164], 0, 1650018110504, 18.131564189005623],
       [2, 10149, 0.5920113921165466, [10144, 10154], 0, 1650018111445, 18.590261928552],
       [3, 10074, 0.2073459029197693, [10069, 10079], 0, 1650018111065, 15.615876690409701],
       [2, 10059, 1.0873171091079712, [10048, 10064], 1, 1650018111445, 14.013141075792857],
       [3, 10028, 0.23533762991428375, [10013, 10033], 0, 1650018111445, 17.857142857142854]],
      [2, 10184, 0.4698709547519684, [10179, 10194], 0, 1650018111813, 18.131564189005623],
      [[2, 10431, 0.27793020009994507, [10421, 10436], 0, 1650018124379, 18.22624721562896],
       [3, 10411, 0.3603847622871399, [10401, 10416], 0, 1650018125129, 20.052982780322065],
       [3, 10290, 0.6246785521507263, [10285, 10300], 0, 1650018124938, 16.63788766523295],
       [2, 10285, 1.1722047328948975, [10275, 10290], 1, 1650018125129, 20.292644917182486],
       [3, 10240, 0.19175183773040771, [10235, 10255], 0, 1650018124938, 17.12124135871018],
       [2, 10205, 2.6698460578918457, [10194, 10210], 1, 1650018125129, 15.408298670179398],
       [2, 10164, 0.3862368166446686, [10154, 10169], 0, 1650018123822, 14.86425861282576],
       [3, 10144, 0.4704577624797821, [10139, 10149], 0, 1650018125129, 16.824958102520323]],
      [3, 10446, 0.3692665696144104, [10441, 10451], 0, 1650018125315, 18.22624721562896]], [
         [[2, 10189, 0.3888215720653534, [10184, 10194], 0, 1650018112005, 18.402983165303734],
          [2, 10159, 0.4286450147628784, [10149, 10164], 0, 1650018112005, 19.753690824899223],
          [3, 10104, 0.5066744089126587, [10094, 10109], 0, 1650018113317, 14.616574804298848],
          [2, 10084, 1.7800346612930298, [10079, 10089], 1, 1650018113317, 14.884913903196171],
          [3, 10048, 0.2888404130935669, [10043, 10053], 0, 1650018112751, 15.268319285223246],
          [2, 10023, 3.41890549659729, [10008, 10028], 1, 1650018113317, 6.693440428380187]],
         [3, 10184, 0.3435825705528259, [10179, 10194], 0, 1650018113506, 19.753690824899223]], [], [], [], [], [
         [[3, 10497, 0.3557647168636322, [10486, 10507], 0, 1650018127752, 22.652223038032158],
          [3, 10411, 0.3603847622871399, [10401, 10416], 0, 1650018125315, 20.277943505860797],
          [3, 10290, 0.6246785521507263, [10285, 10300], 0, 1650018127752, 14.77987343608197],
          [2, 10340, 1.0664786100387573, [10335, 10346], 1, 1650018127752, 16.64892184451224],
          [3, 10280, 0.23783984780311584, [10275, 10285], 0, 1650018127195, 16.76113023097883],
          [2, 10240, 1.0518803596496582, [10225, 10245], 1, 1650018127752, 13.252930533613652],
          [2, 10210, 0.3955329954624176, [10205, 10215], 0, 1650018126819, 14.810690128185367],
          [3, 10184, 0.3423433303833008, [10174, 10194], 0, 1650018127752, 14.426550571507356]],
         [3, 10230, 0.3267088532447815, [10225, 10235], 0, 1650018127943, 14.810690128185367]], [
         [[3, 10502, 0.29758599400520325, [10497, 10512], 0, 1650018128316, 19.274225099158603],
          [2, 10471, 0.2874322831630707, [10461, 10476], 0, 1650018128316, 19.982110211324137],
          [3, 10305, 0.21097131073474884, [10295, 10315], 0, 1650018128501, 13.177375128169915],
          [2, 10351, 2.1101677417755127, [10340, 10356], 1, 1650018128501, 17.225857514421012],
          [3, 10280, 0.23783984780311584, [10275, 10285], 0, 1650018127195, 16.76113023097883],
          [2, 10255, 5.596017360687256, [10245, 10265], 1, 1650018128501, 14.917911168323851],
          [3, 10230, 0.3267088532447815, [10225, 10235], 0, 1650018128124, 15.424035117536237],
          [3, 10184, 0.3423433303833008, [10174, 10194], 0, 1650018127752, 14.426550571507356]],
         [2, 10205, 0.3453388214111328, [10200, 10210], 0, 1650018128689, 14.426550571507356]]]
print(a[1][0][1][5])