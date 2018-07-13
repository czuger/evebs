class AddQuantityToProduceToProductionList < ActiveRecord::Migration[5.2]
  def change
    add_column :production_lists, :quantity_to_produce, :bigint
  end
end
