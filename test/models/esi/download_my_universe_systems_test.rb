require 'test_helper'

class DownloadUniverseSystemsTest < ActiveSupport::TestCase

  def setup
    @universe_list = [ 30001380 ]

    @system_data = JSON.parse(
      <<-ESI_DATA
      {
        "constellation_id": 20000202,
        "name": "Vellaine",
        "security_class": "C",
        "security_status": 0.5811389684677124,
        "star_id": 40087991,
        "stations": [
            60002407
        ],
        "system_id": 30001380
      }
      ESI_DATA
    )

    @station_data = JSON.parse(
      <<-ESI_DATA
      {
        "max_dockable_ship_volume": 50000000,
        "name": "Vellaine VI - Moon 9 - Propel Dynamics Factory",
        "office_rental_cost": 5888879,
        "owner": 1000022,
        "position": {
            "x": -3089478082560,
            "y": 482962022400,
            "z": -2224199147520
        },
        "race_id": 1,
        "reprocessing_efficiency": 0.3,
        "reprocessing_stations_take": 0.05,
        "services": [
            "bounty-missions",
            "courier-missions",
            "interbus",
            "reprocessing-plant",
            "refinery",
            "market",
            "black-market",
            "stock-exchange",
            "cloning",
            "surgery",
            "dna-therapy",
            "repair-facilities",
            "factory",
            "labratory",
            "gambling",
            "fitting",
            "paintshop",
            "news",
            "storage",
            "insurance",
            "docking",
            "office-rental",
            "loyalty-point-store",
            "navy-offices"
        ],
        "station_id": 60002407,
        "system_id": 30001380,
        "type_id": 1529
      }
      ESI_DATA
    )
  end

  test 'Download universe list, then first universe data, then first station data for that universe' do
    dus = Esi::DownloadUniverseSystems.new
    dus.expects(:set_auth_token)
    dus.expects(:get_all_pages).returns(@universe_list )
    dus.stubs(:get_page_retry_on_error).returns(@system_data, @station_data )
    
    dus.update
  end

end