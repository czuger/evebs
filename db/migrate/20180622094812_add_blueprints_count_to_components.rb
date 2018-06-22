class AddBlueprintsCountToComponents < ActiveRecord::Migration[5.2]
  def change
    add_column :components, :blueprints_count, :integer
  end
end
