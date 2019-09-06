(ns codenames_clj.model
  (:require [clojure.zip :as zip]
            [codenames_clj.game :as game]))

(def model-files [["thesauri/th_en_US_new2.dat" 3]
                  ["thesauri/europarl_v6.enthes.txt" 1]
                  ["thesauri/fulllist_appx.txt" 40]
                  ["thesauri/newscomment.txt" 1]
                  ["thesauri/wiki_full_2deg.txt" 100]])
;(def file-weights [3 1 40 1 100])
;(def codenames-list-file (io/resource "wordslist.txt"))                   

(defn thesaurus-file-to-line-pairs
  [fname]
  (->> (clojure.java.io/resource fname)
       (clojure.java.io/reader)
       (line-seq)
       (partition 2)))
       

(defn incorporate-new-line
  [word-graph [[word-w associations-w] m-weight]]
  (let [[word weight-s] (clojure.string/split word-w #"\|")
        weight (Integer/parseInt weight-s)
        associations (clojure.string/split associations-w #"\|")]
    (if (not-any? #(clojure.string/includes? word %) (list "-" " "))
      (reduce (fn [graph new-word]
                
                (if (not-any? #(clojure.string/includes? new-word %) (list "(" " " word))
                  (update-in graph
                    [word new-word]
                    (fn [counter]
                      ;(println weight)
                      (if counter
                        (+ (* m-weight weight) counter)
                        (* m-weight weight)))) 
                  graph))
        
        word-graph
        associations)
      word-graph)))


    

(defn generate-all-models
  [files]
  
  (reduce (fn [model [filename m-weight]]
            ;(println (take 5 (partition 2 (interleave (thesaurus-file-to-line-pairs filename) (repeat m-weight)))))
            (reduce incorporate-new-line
              model
              (partition 2 (interleave (thesaurus-file-to-line-pairs filename) (repeat m-weight)))))
    {}
    files))

    
  

;(def model (range 100))
(def model #(generate-all-models model-files))

