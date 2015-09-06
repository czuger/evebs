require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'

class Crest::AverageMarketPrices

  extend Crest::CrestBase

  def self.update_prices

    manage_cache

    ActiveRecord::Base.transaction do
      CrestCost.find_each do |cc|
        # puts cc.inspect
        # puts cc.eve_item.inspect
        material_missing = false
        cost = 0
        blueprint = cc.eve_item.blueprint
        # puts blueprint.inspect
        next unless blueprint
        blueprint.materials.each do |material|
          # puts "Material = #{material.inspect}"
          component_cpp_eve_item = Component.where(id: material.component_id).pluck( 'cpp_eve_item_id').first
          adjusted_price = CrestCost.where(cpp_item_id: component_cpp_eve_item).pluck( 'adjusted_price' ).first
          if adjusted_price
            cost += adjusted_price*material.required_qtt
          else
            ei = EveItem.find_by_cpp_eve_item_id(component_cpp_eve_item)
            ei_name = ei ? ei.name : component_cpp_eve_item
            puts "No adjusted_price for #{ei_name}"
            material_missing = true
          end
          # break if material_missing
        end
        next if material_missing
        cost *= 1.005 # Pator cost
        cost *= 1.01  # Facility tax
        cc.update_attribute(:cost, cost)
      end
    end
  end

  def self.get_prices

    manage_cache

    html_req = "https://public-crest.eveonline.com/market/prices/"
    # puts html_req
    json_result = open( html_req ).read

    parsed_data = JSON.parse( json_result )

    ActiveRecord::Base.transaction do
      parsed_data['items'].each do |item|
        cpp_item_id = item['type']['id']
        eve_item_id = EveItem.where(cpp_eve_item_id: cpp_item_id).pluck('id').first
        if eve_item_id
          crest_cost = CrestCost.find_by_cpp_item_id( cpp_item_id )
          if crest_cost
            crest_cost.update_attributes(
                adjusted_price: item['adjustedPrice'], average_price: item['averagePrice'], eve_item_id: eve_item_id )
          else
            CrestCost.create!(
                adjusted_price: item['adjustedPrice'], average_price: item['averagePrice'], eve_item_id: eve_item_id, cpp_item_id: cpp_item_id )
          end
        end
      end
    end
  end

end