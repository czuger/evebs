require 'test_helper'

class UpdateDailyTest < ActiveSupport::TestCase

	def setup
		1.upto( Esi::DownloadHistorySetProcessCount::PROCESSES_COUNT ).each do |pc|
			File.open( "data/regional_sales_volumes_#{pc}.json_stream", 'w' )
		end

		File.open( 'data/regional_sales_volumes_1.json_stream', 'w' ) do |f|
			f.puts( '{"cpp_region_id":10000030,"cpp_type_id":12775,"volume":544786,"min":200.9,"max":1149.96,"avg":764.6637037037037}' )
		end

		create( :barrage_l )
		create( :universe_heimatar )
	end

	test 'should add Barrage L for Heimatar in EveMarketHistoriesGroup' do
		assert_changes 'EveMarketHistoriesGroup.all.reload.count' do
			CronProcesses::Daily.update_data
		end
	end

end