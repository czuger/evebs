class AddInvolvedInBlueprintToEveItem < ActiveRecord::Migration[4.2]
  def change
    add_column :eve_items, :involved_in_blueprint, :bool, default: false, index: true
  end
end
