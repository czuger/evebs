class BlueprintComponent < ApplicationRecord

  JITA_EVE_SYSTEM_ID=30000142
  JITA_REGION_CPP_ID=10000002

  has_many :blueprint_materials
  has_many :blueprints, through: :blueprint_materials

  def self.compute_costs
    Banner.p 'Recomputing components costs from Jita prices'

    request = File.open( "#{Rails.root}/sql/update_components_costs.sql" ).read
    ActiveRecord::Base.connection.exec_update( request, :update_components_costs, [ [ nil, Blueprint::TAX_AMOUNT_MULTIPLIER ] ] )
  end
end