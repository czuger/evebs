class AddInformationToEveItemId < ActiveRecord::Migration[5.2]
  def change
    add_column :eve_items, :description, :string
    add_column :eve_items, :additional_information, :jsonb
  end
end
