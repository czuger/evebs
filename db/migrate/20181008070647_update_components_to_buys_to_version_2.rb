class UpdateComponentsToBuysToVersion2 < ActiveRecord::Migration[5.2]
  def change
    drop_table :components_to_buys
    # drop_view :components_to_buys_details, revert_to_version: 1
    create_view :components_to_buys, version: 1
  end
end
