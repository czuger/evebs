class CreateJitaMargins < ActiveRecord::Migration
  def change
    create_table :jita_margins do |t|
      t.references :eve_item, index: true
      t.float :margin

      t.timestamps
    end
  end
end
