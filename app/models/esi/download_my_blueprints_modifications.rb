require_relative 'download'

class Esi::DownloadMyBlueprintsModifications < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
  end

  def update( user )
    ActiveRecord::Base.transaction do

      user.blueprint_modifications.update_all( touched: false )
      download_bp_modifications user
      user.blueprint_modifications.where( touched: false ).delete_all
    end
  end

  private

  def download_bp_modifications( user )
    if user.locked
      puts "#{user.name} is locked. Skipping ..."
      return
    end

    user_id = user.uid
    @rest_url = "characters/#{user_id}/blueprints/"

    return unless set_auth_token( user )

    pages = get_all_pages

    unless pages
      user.update( locked: true )
      return
    end

    ActiveRecord::Base.transaction do
      pages.each do |asset|

        # pp asset

        bp = Blueprint.find_by_cpp_blueprint_id(asset['type_id'])
        next unless bp

        to = BlueprintModification.where( user_id: user.id, blueprint_id: bp.id ).first_or_initialize

        # p asset['material_efficiency']
        modification = ( 100 - asset['material_efficiency'] ) / 100.0

        # In case we have two time the same blueprint with different modifications values we take the best
        if to.percent_modification_value.nil? || to.percent_modification_value > modification
          to.percent_modification_value = modification
        end

        to.touched = true
        to.save!
      end
    end
  end

end