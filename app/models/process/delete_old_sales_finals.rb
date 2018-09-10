module Process

  class DeleteOldSalesFinals

    def self.delete

      Banner.p 'About to delete old sales finals.'

      SalesFinal.where( 'created_at < ?', Time.now - 1.month ).delete_all
    end
  end

end
