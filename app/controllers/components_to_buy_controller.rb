class ComponentsToBuyController < ApplicationController

  def show
    @character.user.production_lists.joins( { eve_item: { blueprint_materials: :blueprint_component } }, { eve_item: :blueprint } )
        .pluck( 'eve_items.name', 'blueprint_components.name', 'blueprints.prod_qtt', :required_qtt )
  end

end
