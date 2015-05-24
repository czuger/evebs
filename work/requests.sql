select * from invTypes t, invMarketGroups g
where t.marketGroupID = g.marketGroupID
and g.marketGroupID in ( 846, 847, 849, 850, 852, 853, 917, 918, 919, 925,
926, 927, 928, 929, 930, 931, 972, 973, 1097, 1195, 1337, 1364, 1368, 1373, 1375,
1377, 1385, 1591, 1883, 400, 401, 402, 403, 433, 434, 435, 436, 449, 450, 452,
421, 422, 423, 424, 1066, 1067, 1068, 1069, 1071, 1072, 1073, 1074, 827, 830, 833, 836,
438, 439, 440, 441, 1081, 1082, 1083, 1084, 1076, 1077, 1078, 1079 );

select * from invTypes t, invMarketGroups g
where t.marketGroupID = g.marketGroupID
and typeName = 'Paladin';

select * from invMarketGroups where description like '%black%';