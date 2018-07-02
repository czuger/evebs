class BlueprintComponent < ApplicationRecord

  JITA_EVE_SYSTEM_ID=30000142
  JITA_REGION_CPP_ID=10000002

  has_many :blueprint_materials
  has_many :blueprints, through: :blueprint_materials

  def self.set_min_prices_for_all_components
    Banner.p 'Recomputing components costs from Jita prices'

    request = File.open( "#{Rails.root}/sql/update_components_costs.sql" ).read
    ActiveRecord::Base.connection.execute( request )
  end
end