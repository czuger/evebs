class RenameShoppingBasketToProductionList < ActiveRecord::Migration[5.2]
  def change
    rename_table :shopping_baskets, :production_lists
  end
end
