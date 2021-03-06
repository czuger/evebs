require 'open-uri'
require 'json'

class Fuzzwork::Blueprints

  def update
    Banner.p 'About to update blueprints'

    begin
      ActiveRecord::Base.transaction do
        sub_update
      end
    rescue => e
      p e.record
      raise e
    end
  end

  private

  def sub_update

    eve_item_cpp_key_to_id = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]
    eve_item_cpp_key_to_name = Hash[ EveItem.pluck( :cpp_eve_item_id, :name ) ]

    max_items_to_check = eve_item_cpp_key_to_id.count
    items_checked = 0

    items_involved_in_blueprints = Set.new

    eve_item_cpp_key_to_id.keys.each do |cpp_id|

      url = "https://www.fuzzwork.co.uk/blueprint/api/blueprint.php?typeid=#{cpp_id}"
      r = JSON.parse(open( url ).read)

      if r['blueprintDetails'] && r['activityMaterials'] && r['activityMaterials'].is_a?( Hash ) && r['activityMaterials']['1']
        # name = r['blueprintDetails']['productTypeName']
        nb_run = r['blueprintDetails']['maxProductionLimit']
        prod_qtt = r['blueprintDetails']['productQuantity']

        # TODO : update involved_in_blueprint for EveItem
        ActiveRecord::Base.transaction do

          eve_item_id = eve_item_cpp_key_to_id[ cpp_id ]
          items_involved_in_blueprints << eve_item_id
          next unless eve_item_id

          blueprint = Blueprint.where( eve_item_id: eve_item_id ).first_or_initialize do |b|
            b.nb_runs = nb_run
            b.prod_qtt = prod_qtt
          end
          blueprint.save!

          r['activityMaterials']['1'].each do |material|
            component_id = material['typeid']

            component = BlueprintComponent.where(cpp_eve_item_id: component_id ).first_or_initialize do |c|
              c.name = eve_item_cpp_key_to_name[ component_id ]
            end
            component.save!
            items_involved_in_blueprints << component.id

            material = BlueprintMaterial.where(blueprint_id: blueprint.id, component_id: component.id ).first_or_initialize do |m|
              m.required_qtt = material['quantity']
            end
            material.save!

          end
        end
      end

      items_checked += 1
      # if items_checked % 100 == 0
      #   puts "#{items_checked} of #{max_items_to_check}" if @de
      # end
    end

    EveItem.update_all( involved_in_blueprint: false )
    EveItem.where( id: items_involved_in_blueprints ).update_all( involved_in_blueprint: true )

  end

end
