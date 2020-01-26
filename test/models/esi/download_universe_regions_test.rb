require 'test_helper'

class DownloadUniverseRegionsTest < ActiveSupport::TestCase

	def setup
		@regions_list = [ 10000001 ]
		@region_hash = { 'constellations' => [ 20000001 ] }
		@constellation_hash = { 'name' => 'San Matar', 'systems' => [ 30000001 ] }
		@system_hash = { 'name' => 'Tanoo', 'stations' => [ 60012526 ] }
		@station_hash = { 'name' => 'Tanoo V - Moon 1 - Ammatar Consulate Bureau' }
	end


	test 'Do full download' do
		dus = Esi::DownloadUniverseRegions.new

		# dus.expects(:set_auth_token)
		dus.expects(:get_all_pages).returns(@regions_list )

		dus.expects(:get_page<_retry_on_error).with( expect: :region ).returns(@region_hash )

		dus.expects(:get_page_retry_on_error).with( expect: :constellation ).returns(@constellation_hash )

		dus.expects(:get_page_retry_on_error).with( expect: :system ).returns(@system_hash )

		dus.expects(:get_page_retry_on_error).with( expect: :station ).returns(@station_hash )

		dus.download
	end

end