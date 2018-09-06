module Libs

  class BatchInsertBuffer

    def initialize( class_name )
      @batch_buffer = []
      @class_name = class_name
    end

    def add_data( data )
      @batch_buffer << data
      flush_buffer if @batch_buffer.count > 5000
    end

    def flush_buffer
      @class_name.constantize.import( @batch_buffer )
      @batch_buffer.clear
    end
  end

end
