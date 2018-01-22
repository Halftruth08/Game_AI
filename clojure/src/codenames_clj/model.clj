(ns codenames-clj.model)

(def model-files #{"thesauri/th_en_US_new2.dat"
                   "thesauri/europarl-v6.enthes.txt"
                   "thesauri/fulllist_appx.txt"
                   "thesauri/newscomment.txt"
                   "thesauri/wiki_full_2deg.txt"
                   })

(defn thesaurus-file-to-line-pairs
  [fname]
  (->> (clojure.java.io/resource fname)
       (clojure.java.io/reader)
       (line-seq)
       (partition 2)))

(defn incorporate-new-line
  [word-graph [word-w associations-w]]
  (let [[word weight-s] (clojure.string/split word-w #"\|")
        weight (Integer/parseInt weight-s)
        associations (clojure.string/split associations-w #"\|")]
    (reduce (fn [graph new-word]
              (update-in graph
                         [word new-word]
                         (fn [counter]
                           (if counter
                             (+ counter weight)
                             weight))))
            word-graph
            associations)))

(defn generate-all-models
  []
  (reduce (fn [model filename]
            (reduce incorporate-new-line
                    model
                    (thesaurus-file-to-line-pairs filename)))
          {}
          model-files))

(time (def model (generate-all-models)))

