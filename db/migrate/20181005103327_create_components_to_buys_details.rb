class CreateComponentsToBuysDetails < ActiveRecord::Migration[5.2]
  def change
    create_view :components_to_buys_details
  end
end
