require 'open-uri'
require 'open-uri/cached'
require 'pp'

# Items list from CREST is not really reliable.
# Use ItemsInit::ItemsList.initialize_eve_items rather
# That was because i was only reading the first page

class Crest::EveItemsFromCrest
  include Crest::CrestBase

  def initialize

    # TODO : il faut mettre a jour la liste des groupes avant

    ActiveRecord::Base.transaction do

      items = get_multipage_data( 'market/types', true )
      items_hash = {}

      items.each do |e|

        market_group_id = e['marketGroup']['id']
        cpp_type_id = e['type']['id']
        name = e['type']['name']
        lcase_name = name.downcase

        if ALLOWED_GROUPS.include?( market_group_id )
          items_hash[ cpp_type_id ] = [ market_group_id, cpp_type_id, name ]
        end
      end
      items = nil # we do not require items anymore, so we delete it in order to allow the garbage collector to free it

      # Purge nonexisting items
      # Get all items ids
      cpp_eve_items_ids = EveItem.all.pluck( :cpp_eve_item_id ).to_a
      # Remove items we will keep
      cpp_eve_items_ids.reject!{ |e| items_hash.has_key?( e ) }
      # Get the name of the items we will delete
      to_delete_items_name = EveItem.where( cpp_eve_item_id: cpp_eve_items_ids ).pluck( :name ).to_a
      to_delete_items_name.each do |name|
        puts "About to delete #{name}"
      end
      to_delete_items_name = nil # Mark space as unused

      to_delete_items_ids = EveItem.where( cpp_eve_item_id: cpp_eve_items_ids ).pluck( :id ).to_a
      CrestPriceHistory.delete_all( eve_item_id: to_delete_items_ids )
      CrestPricesLastMonthAverage.delete_all( eve_item_id: to_delete_items_ids )
      EveItem.delete_all( id: to_delete_items_ids )

      # Add new items
      items_hash.each do |key, item_array|

        market_group_id = item_array[0]
        cpp_type_id = item_array[1]
        name = item_array[2]
        lcase_name = name.downcase

        eve_item = EveItem.find_by_cpp_eve_item_id( cpp_type_id )

        if eve_item
          puts "Updating #{eve_item.name}"
          eve_item.update_attributes( market_group_id: market_group_id, name: name, name_lowcase: lcase_name )
        else
          puts "Creating an entry for #{name}"
          EveItem.create!( cpp_eve_item_id: type_id, name: name, name_lowcase: lcase_name, market_group_id: market_group_id )
        end
      end
    end
  end

  def print_all_groups
    File.open( 'tmp/groups.txt', 'w' ) do |file|
      MarketGroup.leaves.each do |leave|
        bread = leave.get_market_group_breadcrumb
        file.puts "#{leave.cpp_market_group_id}\t#{bread}"
      end
    end
  end

  ALLOWED_GROUPS = [ 1009,1010,1011,1012,1013,1014,1015,102,1027,103,1033,1037,1038,1039,1040,1048,1049,105,1050,1051,
    1052,1053,1054,1055,1056,1057,1058,1059,106,1060,1061,1062,1063,1066,1067,1068,1069,107,1071,1072,1073,1074,1076,1077,
    1078,1079,108,1081,1082,1083,1084,1085,1086,1087,1088,109,1090,1091,1092,1093,1103,112,1122,1123,1124,1125,1126,1127,
    1128,1129,113,1130,1131,1132,1133,1134,1135,1136,1137,1139,1140,1141,1142,1147,116,1193,1194,1195,1196,1197,1199,1200,
    1201,1206,1207,1208,1210,1211,1212,1213,1214,1215,1219,1220,1221,1222,1223,1224,1225,1226,1227,1228,1229,1230,1231,1232,
    1233,1234,1235,1236,1237,1238,1239,126,1273,1274,1275,1282,1283,1284,1287,131,1310,1317,1333,1334,1335,1336,1337,139,
    1390,1416,1426,158,1598,1599,1600,1611,1616,1628,1629,1630,1631,1634,1635,1636,1637,1638,1639,1640,1641,1642,1646,1650,
    1651,1652,1653,1657,1658,1665,1666,1667,1668,1669,1670,1672,1673,1674,1675,1676,1678,1679,1680,1681,1682,1683,1684,1685,
    1686,1687,1688,1689,1690,1691,1692,1693,1694,1695,1696,1702,1709,1715,1717,1718,1730,1731,1732,1733,1734,1735,1736,1737,
    1739,1740,1782,1783,1784,1785,1786,1787,1788,1789,1790,1791,1792,1793,1816,1817,1818,1819,1827,1831,1832,1833,1835,1844,
    1845,1847,1855,1856,1857,1858,1859,1860,1862,1863,1864,1865,1866,1867,1868,1869,1870,1873,1880,1884,1885,1886,1887,1888,
    1889,1907,1908,1909,1921,1924,1931,1935,1936,1937,1941,1950,1952,1953,2018,2021,2032,2033,2034,380,381,382,383,393,394,
    395,396,400,401,402,403,405,421,422,423,424,433,434,435,436,438,439,440,441,449,450,451,452,465,466,467,468,470,471,472,
    473,478,479,481,482,483,484,485,488,490,494,499,500,501,502,503,504,506,512,514,515,516,517,518,519,521,522,523,525,526,
    527,528,529,530,542,561,562,563,564,565,566,567,568,569,570,572,573,574,575,576,577,578,579,593,594,595,596,600,601,602,
    603,604,605,606,608,609,61,610,611,612,613,615,630,631,632,633,639,64,640,641,642,643,644,645,646,647,648,658,659,660,
    665,666,667,669,670,671,672,673,675,676,678,679,680,683,686,687,688,689,690,691,692,693,694,695,696,697,698,699,700,701,
    702,703,704,705,706,707,708,711,712,713,714,715,716,717,718,719,72,720,721,722,723,724,725,726,727,728,729,73,74,75,757,
    76,762,763,764,765,767,768,769,77,770,771,772,773,774,775,776,777,778,78,781,79,80,801,802,803,81,813,814,815,816,818,819,
    82,820,821,825,826,827,828,829,83,830,831,832,833,834,835,836,837,838,839,84,840,841,842,843,85,854,855,856,857,858,859,860,
    861,862,863,864,865,866,867,868,869,870,871,872,874,910,911,912,914,917,918,919,920,921,922,923,924,925,926,927,928,929,930,
    931,932,933,935,938,967,971,972,973,974,983 ]

end