class CreateComponentToBuys < ActiveRecord::Migration[5.2]
  def change
    create_view :component_to_buys
  end
end
