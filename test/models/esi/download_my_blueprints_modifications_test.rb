require 'test_helper'

require_relative 'esi_open_url_request_result'

class DownloadMyBlueprintsModificationsTest < ActiveSupport::TestCase

  def setup
    @user = create( :user )

    @bp = create( :blueprint )

    blueprint_type = EsiOpenUrlRequestResult.new(
        [ { 'type_id' => @bp.cpp_blueprint_id, 'material_efficiency' => 3 } ], add_random_name_to_data: false )

    @ub = Esi::DownloadMyBlueprintsModifications.new
    @ub.expects( :set_auth_token ).returns( true )
    @ub.expects( :open ).with(regexp_matches( /characters\/.*\/blueprints/ ) ).returns( blueprint_type )
  end

  test 'create blueprint modification entry' do
    assert_changes 'BlueprintModification.count' do
      @ub.update( @user )
    end
  end

  test 'update blueprint modification entry' do
    bm = BlueprintModification.create!(
                             user_id: @user.id, blueprint_id: @bp.id, percent_modification_value: 0.99
    )
    assert_no_changes 'BlueprintModification.count' do
      @ub.update( @user )
    end

    assert_equal 0.97, bm.reload.percent_modification_value

  end

end