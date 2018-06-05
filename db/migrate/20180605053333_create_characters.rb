class CreateCharacters < ActiveRecord::Migration[5.2]
  def change
    create_table :characters do |t|
      t.references :user, null: false, foreign_key: true
      t.string :name, null: false
      t.integer :eve_id, null: false, index: { unique: true }
      t.datetime :expire_at, null: false

      t.timestamps
    end
  end
end
