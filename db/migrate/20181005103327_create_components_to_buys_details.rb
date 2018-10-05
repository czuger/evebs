class CreateComponentsToBuysDetails < ActiveRecord::Migration[5.2]
  def change
    create_view :components_to_buys_details
    drop_view :component_to_buys, revert_to_version: 10
  end
end
